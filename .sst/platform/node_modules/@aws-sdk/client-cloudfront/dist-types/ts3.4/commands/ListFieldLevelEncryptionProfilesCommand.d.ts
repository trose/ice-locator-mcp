import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import {
  ListFieldLevelEncryptionProfilesRequest,
  ListFieldLevelEncryptionProfilesResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface ListFieldLevelEncryptionProfilesCommandInput
  extends ListFieldLevelEncryptionProfilesRequest {}
export interface ListFieldLevelEncryptionProfilesCommandOutput
  extends ListFieldLevelEncryptionProfilesResult,
    __MetadataBearer {}
export declare class ListFieldLevelEncryptionProfilesCommand extends $Command<
  ListFieldLevelEncryptionProfilesCommandInput,
  ListFieldLevelEncryptionProfilesCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: ListFieldLevelEncryptionProfilesCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: ListFieldLevelEncryptionProfilesCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    ListFieldLevelEncryptionProfilesCommandInput,
    ListFieldLevelEncryptionProfilesCommandOutput
  >;
  private serialize;
  private deserialize;
}
