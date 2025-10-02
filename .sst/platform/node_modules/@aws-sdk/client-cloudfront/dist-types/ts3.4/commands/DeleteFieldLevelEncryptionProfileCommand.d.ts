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
import { DeleteFieldLevelEncryptionProfileRequest } from "../models/models_1";
export { __MetadataBearer, $Command };
export interface DeleteFieldLevelEncryptionProfileCommandInput
  extends DeleteFieldLevelEncryptionProfileRequest {}
export interface DeleteFieldLevelEncryptionProfileCommandOutput
  extends __MetadataBearer {}
export declare class DeleteFieldLevelEncryptionProfileCommand extends $Command<
  DeleteFieldLevelEncryptionProfileCommandInput,
  DeleteFieldLevelEncryptionProfileCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: DeleteFieldLevelEncryptionProfileCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: DeleteFieldLevelEncryptionProfileCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    DeleteFieldLevelEncryptionProfileCommandInput,
    DeleteFieldLevelEncryptionProfileCommandOutput
  >;
  private serialize;
  private deserialize;
}
