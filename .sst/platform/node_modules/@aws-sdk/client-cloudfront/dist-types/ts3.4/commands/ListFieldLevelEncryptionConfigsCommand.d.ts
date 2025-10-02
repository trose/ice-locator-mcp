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
  ListFieldLevelEncryptionConfigsRequest,
  ListFieldLevelEncryptionConfigsResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface ListFieldLevelEncryptionConfigsCommandInput
  extends ListFieldLevelEncryptionConfigsRequest {}
export interface ListFieldLevelEncryptionConfigsCommandOutput
  extends ListFieldLevelEncryptionConfigsResult,
    __MetadataBearer {}
export declare class ListFieldLevelEncryptionConfigsCommand extends $Command<
  ListFieldLevelEncryptionConfigsCommandInput,
  ListFieldLevelEncryptionConfigsCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: ListFieldLevelEncryptionConfigsCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: ListFieldLevelEncryptionConfigsCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    ListFieldLevelEncryptionConfigsCommandInput,
    ListFieldLevelEncryptionConfigsCommandOutput
  >;
  private serialize;
  private deserialize;
}
