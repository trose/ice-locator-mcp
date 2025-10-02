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
  GetFieldLevelEncryptionProfileRequest,
  GetFieldLevelEncryptionProfileResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetFieldLevelEncryptionProfileCommandInput
  extends GetFieldLevelEncryptionProfileRequest {}
export interface GetFieldLevelEncryptionProfileCommandOutput
  extends GetFieldLevelEncryptionProfileResult,
    __MetadataBearer {}
export declare class GetFieldLevelEncryptionProfileCommand extends $Command<
  GetFieldLevelEncryptionProfileCommandInput,
  GetFieldLevelEncryptionProfileCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetFieldLevelEncryptionProfileCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetFieldLevelEncryptionProfileCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    GetFieldLevelEncryptionProfileCommandInput,
    GetFieldLevelEncryptionProfileCommandOutput
  >;
  private serialize;
  private deserialize;
}
